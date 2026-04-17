package dns

import (
	"context"
	"fmt"
	"net"
	"strings"
	"time"
)

type RecordType string

const (
	TypeA     RecordType = "A"
	TypeAAAA  RecordType = "AAAA"
	TypeMX    RecordType = "MX"
	TypeNS    RecordType = "NS"
	TypeCNAME RecordType = "CNAME"
	TypeTXT   RecordType = "TXT"
	TypePTR   RecordType = "PTR"
)

var validTypes = map[RecordType]bool{
	TypeA: true, TypeAAAA: true, TypeMX: true,
	TypeNS: true, TypeCNAME: true, TypeTXT: true,
}

type Record struct {
	Type  RecordType
	Value string
}

type Result struct {
	Domain  string
	Records []Record
	Elapsed time.Duration
}

func Lookup(domain string, types []string) (*Result, error) {
	if len(types) == 0 {
		types = []string{"A", "AAAA", "CNAME", "MX", "NS", "TXT"}
	}

	// 未知のタイプを事前に reject
	for _, t := range types {
		rt := RecordType(strings.ToUpper(t))
		if !validTypes[rt] {
			return nil, fmt.Errorf("unsupported record type: %s (supported: A, AAAA, MX, NS, CNAME, TXT)", t)
		}
	}

	resolver := &net.Resolver{PreferGo: true}
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	start := time.Now()
	result := &Result{Domain: domain}

	var lastErr error
	successCount := 0

	for _, t := range types {
		records, err := lookupType(ctx, resolver, domain, RecordType(strings.ToUpper(t)))
		if err != nil {
			lastErr = err
			continue
		}
		successCount++
		result.Records = append(result.Records, records...)
	}

	// 全タイプが失敗した場合はエラーを返す
	if successCount == 0 && lastErr != nil {
		return nil, fmt.Errorf("all lookups failed for %s: %w", domain, lastErr)
	}

	result.Elapsed = time.Since(start)
	return result, nil
}

func LookupReverse(ip string) (*Result, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	start := time.Now()
	resolver := &net.Resolver{PreferGo: true}

	names, err := resolver.LookupAddr(ctx, ip)
	if err != nil {
		return nil, fmt.Errorf("reverse lookup failed: %w", err)
	}

	result := &Result{Domain: ip}
	for _, name := range names {
		result.Records = append(result.Records, Record{Type: TypePTR, Value: name})
	}
	result.Elapsed = time.Since(start)
	return result, nil
}

func lookupType(ctx context.Context, r *net.Resolver, domain string, t RecordType) ([]Record, error) {
	var records []Record
	switch t {
	case TypeA:
		addrs, err := r.LookupHost(ctx, domain)
		if err != nil {
			return nil, err
		}
		for _, addr := range addrs {
			if net.ParseIP(addr).To4() != nil {
				records = append(records, Record{Type: TypeA, Value: addr})
			}
		}
	case TypeAAAA:
		addrs, err := r.LookupHost(ctx, domain)
		if err != nil {
			return nil, err
		}
		for _, addr := range addrs {
			if net.ParseIP(addr).To4() == nil && net.ParseIP(addr).To16() != nil {
				records = append(records, Record{Type: TypeAAAA, Value: addr})
			}
		}
	case TypeMX:
		mxs, err := r.LookupMX(ctx, domain)
		if err != nil {
			return nil, err
		}
		for _, mx := range mxs {
			records = append(records, Record{Type: TypeMX, Value: fmt.Sprintf("%d %s", mx.Pref, mx.Host)})
		}
	case TypeNS:
		nss, err := r.LookupNS(ctx, domain)
		if err != nil {
			return nil, err
		}
		for _, ns := range nss {
			records = append(records, Record{Type: TypeNS, Value: ns.Host})
		}
	case TypeCNAME:
		cname, err := r.LookupCNAME(ctx, domain)
		if err != nil {
			return nil, err
		}
		if cname != domain+"." {
			records = append(records, Record{Type: TypeCNAME, Value: cname})
		}
	case TypeTXT:
		txts, err := r.LookupTXT(ctx, domain)
		if err != nil {
			return nil, err
		}
		for _, txt := range txts {
			records = append(records, Record{Type: TypeTXT, Value: txt})
		}
	}
	return records, nil
}
